// Copyright (c) TwistedFTW
// See LICENSE for details.

var main = angular.module('main', []);

main.run(function($templateCache) {
    var templates = document.getElementsByTagName('template');
    angular.forEach(templates, function(tmpl) {
        $templateCache.put(tmpl.getAttribute('name'), tmpl.innerHTML);
    })
});

main.factory('ArticleIndex', function($http) {
    return $http.get('article_index.json')
        .then(function(d) {
            return d.data;
        });
});

main.controller('TutorialCtrl', function($scope, ArticleIndex) {
    $scope.index = ArticleIndex;
});

main.directive('linkList', function(ArticleIndex) {
    return {
        restrict: 'E',
        template: '<ul>' +
            '<li ng-repeat="link in index[section][\'articles\']">' +
                '<a href="articles.html#!/{{ section }}/{{ link.name }}">' +
                    '{{ link.title }}' +
                '</a>' +
            '</li></ul>',
        scope: {
            'index': '=',
            'section': '@'
        }
    }
});

main.controller('CarouselCtrl', function($scope, $timeout, $templateCache) {
    $scope.showing = {
        ability: '',
        content: '',
    }
    $scope.slides = [
        'staticweb-server',
        'irc-server',
        'run-trial',
    ];
    $scope.index = 0;
    $scope.paused = false;

    $scope.next = function() {
        $scope.index += 1;
        if ($scope.index >= $scope.slides.length) {
            $scope.index = 0;
        }
    }
    $scope.prev = function() {
        $scope.index -= 1;
        if ($scope.index < 0) {
            $scope.index = $scope.slides.length-1;
        }
    }

    $scope.$watch('index', function() {
        var slide = $scope.slides[$scope.index];
        $scope.showing.ability = $templateCache.get(slide + '.title');
        $scope.showing.content = $templateCache.get(slide + '.html');
    })

    $scope.fuse = function() {
        return $timeout(function() {
            if ($scope.paused) {
                return;
            }
            $scope.next();
        }, 5000).then(function() {
            $scope.fuse();
        });
    }
    $scope.fuse();
})